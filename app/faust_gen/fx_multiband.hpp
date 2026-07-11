/* ------------------------------------------------------------
name: "fx_multiband"
Code generated with Faust 2.70.3 (https://faust.grame.fr)
Compilation options: -lang cpp -ct 1 -cn FxMultiband -es 1 -mcd 16 -mdd 1024 -mdy 33 -single -ftz 0
------------------------------------------------------------ */

#ifndef  __FxMultiband_H__
#define  __FxMultiband_H__

#ifndef FAUSTFLOAT
#define FAUSTFLOAT float
#endif 

#include <algorithm>
#include <cmath>
#include <cstdint>
#include <math.h>

#ifndef FAUSTCLASS 
#define FAUSTCLASS FxMultiband
#endif

#ifdef __APPLE__ 
#define exp10f __exp10f
#define exp10 __exp10
#endif

#if defined(_WIN32)
#define RESTRICT __restrict
#else
#define RESTRICT __restrict__
#endif

static float FxMultiband_faustpower2_f(float value) {
	return value * value;
}

class FxMultiband : public dsp {
	
 private:
	
	FAUSTFLOAT fHslider0;
	int fSampleRate;
	float fConst1;
	float fRec1[3];
	float fRec0[3];
	FAUSTFLOAT fHslider1;
	float fConst2;
	FAUSTFLOAT fHslider2;
	float fRec5[3];
	float fRec4[3];
	FAUSTFLOAT fHslider3;
	float fRec3[2];
	FAUSTFLOAT fHslider4;
	float fRec2[2];
	FAUSTFLOAT fHslider5;
	FAUSTFLOAT fHslider6;
	float fRec11[3];
	float fRec10[3];
	float fRec9[3];
	float fRec8[3];
	float fRec15[3];
	float fRec14[3];
	float fRec13[3];
	float fRec12[3];
	float fRec7[2];
	FAUSTFLOAT fHslider7;
	float fRec6[2];
	FAUSTFLOAT fHslider8;
	float fRec18[3];
	float fRec19[3];
	float fRec17[2];
	FAUSTFLOAT fHslider9;
	float fRec16[2];
	float fConst3;
	float fConst4;
	FAUSTFLOAT fHslider10;
	float fRec20[2];
	
 public:
	FxMultiband() {}

	void metadata(Meta* m) { 
		m->declare("analyzers.lib/amp_follower_ar:author", "Jonatan Liljedahl, revised by Romain Michon");
		m->declare("analyzers.lib/name", "Faust Analyzer Library");
		m->declare("analyzers.lib/version", "1.2.0");
		m->declare("basics.lib/name", "Faust Basic Element Library");
		m->declare("basics.lib/tabulateNd", "Copyright (C) 2023 Bart Brouns <bart@magnetophon.nl>");
		m->declare("basics.lib/version", "1.12.0");
		m->declare("compile_options", "-lang cpp -ct 1 -cn FxMultiband -es 1 -mcd 16 -mdd 1024 -mdy 33 -single -ftz 0");
		m->declare("compressors.lib/compression_gain_mono:author", "Julius O. Smith III");
		m->declare("compressors.lib/compression_gain_mono:copyright", "Copyright (C) 2014-2020 by Julius O. Smith III <jos@ccrma.stanford.edu>");
		m->declare("compressors.lib/compression_gain_mono:license", "MIT-style STK-4.3 license");
		m->declare("compressors.lib/compressor_stereo:author", "Julius O. Smith III");
		m->declare("compressors.lib/compressor_stereo:copyright", "Copyright (C) 2014-2020 by Julius O. Smith III <jos@ccrma.stanford.edu>");
		m->declare("compressors.lib/compressor_stereo:license", "MIT-style STK-4.3 license");
		m->declare("compressors.lib/name", "Faust Compressor Effect Library");
		m->declare("compressors.lib/version", "1.6.0");
		m->declare("filename", "fx_multiband.dsp");
		m->declare("filters.lib/fir:author", "Julius O. Smith III");
		m->declare("filters.lib/fir:copyright", "Copyright (C) 2003-2019 by Julius O. Smith III <jos@ccrma.stanford.edu>");
		m->declare("filters.lib/fir:license", "MIT-style STK-4.3 license");
		m->declare("filters.lib/highpass:author", "Julius O. Smith III");
		m->declare("filters.lib/highpass:copyright", "Copyright (C) 2003-2019 by Julius O. Smith III <jos@ccrma.stanford.edu>");
		m->declare("filters.lib/iir:author", "Julius O. Smith III");
		m->declare("filters.lib/iir:copyright", "Copyright (C) 2003-2019 by Julius O. Smith III <jos@ccrma.stanford.edu>");
		m->declare("filters.lib/iir:license", "MIT-style STK-4.3 license");
		m->declare("filters.lib/lowpass0_highpass1", "Copyright (C) 2003-2019 by Julius O. Smith III <jos@ccrma.stanford.edu>");
		m->declare("filters.lib/lowpass0_highpass1:author", "Julius O. Smith III");
		m->declare("filters.lib/lowpass:author", "Julius O. Smith III");
		m->declare("filters.lib/lowpass:copyright", "Copyright (C) 2003-2019 by Julius O. Smith III <jos@ccrma.stanford.edu>");
		m->declare("filters.lib/lowpass:license", "MIT-style STK-4.3 license");
		m->declare("filters.lib/name", "Faust Filters Library");
		m->declare("filters.lib/tf2:author", "Julius O. Smith III");
		m->declare("filters.lib/tf2:copyright", "Copyright (C) 2003-2019 by Julius O. Smith III <jos@ccrma.stanford.edu>");
		m->declare("filters.lib/tf2:license", "MIT-style STK-4.3 license");
		m->declare("filters.lib/tf2s:author", "Julius O. Smith III");
		m->declare("filters.lib/tf2s:copyright", "Copyright (C) 2003-2019 by Julius O. Smith III <jos@ccrma.stanford.edu>");
		m->declare("filters.lib/tf2s:license", "MIT-style STK-4.3 license");
		m->declare("filters.lib/version", "1.3.0");
		m->declare("maths.lib/author", "GRAME");
		m->declare("maths.lib/copyright", "GRAME");
		m->declare("maths.lib/license", "LGPL with exception");
		m->declare("maths.lib/name", "Faust Math Library");
		m->declare("maths.lib/version", "2.7.0");
		m->declare("name", "fx_multiband");
		m->declare("platform.lib/name", "Generic Platform Library");
		m->declare("platform.lib/version", "1.3.0");
		m->declare("signals.lib/name", "Faust Signal Routing Library");
		m->declare("signals.lib/onePoleSwitching:author", "Jonatan Liljedahl, revised by Dario Sanfilippo");
		m->declare("signals.lib/onePoleSwitching:licence", "STK-4.3");
		m->declare("signals.lib/version", "1.5.0");
	}

	virtual int getNumInputs() {
		return 2;
	}
	virtual int getNumOutputs() {
		return 2;
	}
	
	static void classInit(int sample_rate) {
	}
	
	virtual void instanceConstants(int sample_rate) {
		fSampleRate = sample_rate;
		float fConst0 = std::min<float>(1.92e+05f, std::max<float>(1.0f, float(fSampleRate)));
		fConst1 = 3.1415927f / fConst0;
		fConst2 = 1.0f / fConst0;
		fConst3 = 44.1f / fConst0;
		fConst4 = 1.0f - fConst3;
	}
	
	virtual void instanceResetUserInterface() {
		fHslider0 = FAUSTFLOAT(2.5e+03f);
		fHslider1 = FAUSTFLOAT(2e+01f);
		fHslider2 = FAUSTFLOAT(-18.0f);
		fHslider3 = FAUSTFLOAT(1.5e+02f);
		fHslider4 = FAUSTFLOAT(2.0f);
		fHslider5 = FAUSTFLOAT(-18.0f);
		fHslider6 = FAUSTFLOAT(1.5e+02f);
		fHslider7 = FAUSTFLOAT(2.0f);
		fHslider8 = FAUSTFLOAT(-18.0f);
		fHslider9 = FAUSTFLOAT(2.0f);
		fHslider10 = FAUSTFLOAT(0.0f);
	}
	
	virtual void instanceClear() {
		for (int l0 = 0; l0 < 3; l0 = l0 + 1) {
			fRec1[l0] = 0.0f;
		}
		for (int l1 = 0; l1 < 3; l1 = l1 + 1) {
			fRec0[l1] = 0.0f;
		}
		for (int l2 = 0; l2 < 3; l2 = l2 + 1) {
			fRec5[l2] = 0.0f;
		}
		for (int l3 = 0; l3 < 3; l3 = l3 + 1) {
			fRec4[l3] = 0.0f;
		}
		for (int l4 = 0; l4 < 2; l4 = l4 + 1) {
			fRec3[l4] = 0.0f;
		}
		for (int l5 = 0; l5 < 2; l5 = l5 + 1) {
			fRec2[l5] = 0.0f;
		}
		for (int l6 = 0; l6 < 3; l6 = l6 + 1) {
			fRec11[l6] = 0.0f;
		}
		for (int l7 = 0; l7 < 3; l7 = l7 + 1) {
			fRec10[l7] = 0.0f;
		}
		for (int l8 = 0; l8 < 3; l8 = l8 + 1) {
			fRec9[l8] = 0.0f;
		}
		for (int l9 = 0; l9 < 3; l9 = l9 + 1) {
			fRec8[l9] = 0.0f;
		}
		for (int l10 = 0; l10 < 3; l10 = l10 + 1) {
			fRec15[l10] = 0.0f;
		}
		for (int l11 = 0; l11 < 3; l11 = l11 + 1) {
			fRec14[l11] = 0.0f;
		}
		for (int l12 = 0; l12 < 3; l12 = l12 + 1) {
			fRec13[l12] = 0.0f;
		}
		for (int l13 = 0; l13 < 3; l13 = l13 + 1) {
			fRec12[l13] = 0.0f;
		}
		for (int l14 = 0; l14 < 2; l14 = l14 + 1) {
			fRec7[l14] = 0.0f;
		}
		for (int l15 = 0; l15 < 2; l15 = l15 + 1) {
			fRec6[l15] = 0.0f;
		}
		for (int l16 = 0; l16 < 3; l16 = l16 + 1) {
			fRec18[l16] = 0.0f;
		}
		for (int l17 = 0; l17 < 3; l17 = l17 + 1) {
			fRec19[l17] = 0.0f;
		}
		for (int l18 = 0; l18 < 2; l18 = l18 + 1) {
			fRec17[l18] = 0.0f;
		}
		for (int l19 = 0; l19 < 2; l19 = l19 + 1) {
			fRec16[l19] = 0.0f;
		}
		for (int l20 = 0; l20 < 2; l20 = l20 + 1) {
			fRec20[l20] = 0.0f;
		}
	}
	
	virtual void init(int sample_rate) {
		classInit(sample_rate);
		instanceInit(sample_rate);
	}
	
	virtual void instanceInit(int sample_rate) {
		instanceConstants(sample_rate);
		instanceResetUserInterface();
		instanceClear();
	}
	
	virtual FxMultiband* clone() {
		return new FxMultiband();
	}
	
	virtual int getSampleRate() {
		return fSampleRate;
	}
	
	virtual void buildUserInterface(UI* ui_interface) {
		ui_interface->openVerticalBox("fx_multiband");
		ui_interface->addHorizontalSlider("attack", &fHslider1, FAUSTFLOAT(2e+01f), FAUSTFLOAT(1.0f), FAUSTFLOAT(1.2e+02f), FAUSTFLOAT(1.0f));
		ui_interface->addHorizontalSlider("high_ratio", &fHslider4, FAUSTFLOAT(2.0f), FAUSTFLOAT(1.0f), FAUSTFLOAT(8.0f), FAUSTFLOAT(0.1f));
		ui_interface->addHorizontalSlider("high_thresh", &fHslider2, FAUSTFLOAT(-18.0f), FAUSTFLOAT(-48.0f), FAUSTFLOAT(0.0f), FAUSTFLOAT(0.5f));
		ui_interface->addHorizontalSlider("low_ratio", &fHslider9, FAUSTFLOAT(2.0f), FAUSTFLOAT(1.0f), FAUSTFLOAT(8.0f), FAUSTFLOAT(0.1f));
		ui_interface->addHorizontalSlider("low_thresh", &fHslider8, FAUSTFLOAT(-18.0f), FAUSTFLOAT(-48.0f), FAUSTFLOAT(0.0f), FAUSTFLOAT(0.5f));
		ui_interface->addHorizontalSlider("makeup", &fHslider10, FAUSTFLOAT(0.0f), FAUSTFLOAT(-12.0f), FAUSTFLOAT(12.0f), FAUSTFLOAT(0.1f));
		ui_interface->addHorizontalSlider("mid_ratio", &fHslider7, FAUSTFLOAT(2.0f), FAUSTFLOAT(1.0f), FAUSTFLOAT(8.0f), FAUSTFLOAT(0.1f));
		ui_interface->addHorizontalSlider("mid_thresh", &fHslider5, FAUSTFLOAT(-18.0f), FAUSTFLOAT(-48.0f), FAUSTFLOAT(0.0f), FAUSTFLOAT(0.5f));
		ui_interface->addHorizontalSlider("release", &fHslider3, FAUSTFLOAT(1.5e+02f), FAUSTFLOAT(2e+01f), FAUSTFLOAT(8e+02f), FAUSTFLOAT(1.0f));
		ui_interface->addHorizontalSlider("xhigh", &fHslider0, FAUSTFLOAT(2.5e+03f), FAUSTFLOAT(8e+02f), FAUSTFLOAT(9e+03f), FAUSTFLOAT(1.0f));
		ui_interface->addHorizontalSlider("xlow", &fHslider6, FAUSTFLOAT(1.5e+02f), FAUSTFLOAT(4e+01f), FAUSTFLOAT(5e+02f), FAUSTFLOAT(1.0f));
		ui_interface->closeBox();
	}
	
	virtual void compute(int count, FAUSTFLOAT** RESTRICT inputs, FAUSTFLOAT** RESTRICT outputs) {
		FAUSTFLOAT* input0 = inputs[0];
		FAUSTFLOAT* input1 = inputs[1];
		FAUSTFLOAT* output0 = outputs[0];
		FAUSTFLOAT* output1 = outputs[1];
		float fSlow0 = std::tan(fConst1 * float(fHslider0));
		float fSlow1 = FxMultiband_faustpower2_f(fSlow0);
		float fSlow2 = 1.0f / fSlow1;
		float fSlow3 = 2.0f * (1.0f - fSlow2);
		float fSlow4 = 1.0f / fSlow0;
		float fSlow5 = (fSlow4 + -1.4142135f) / fSlow0 + 1.0f;
		float fSlow6 = (fSlow4 + 1.4142135f) / fSlow0 + 1.0f;
		float fSlow7 = 1.0f / fSlow6;
		float fSlow8 = float(fHslider1);
		float fSlow9 = 0.0005f * fSlow8;
		int iSlow10 = std::fabs(fSlow9) < 1.1920929e-07f;
		float fSlow11 = ((iSlow10) ? 0.0f : std::exp(-(fConst2 / ((iSlow10) ? 1.0f : fSlow9))));
		float fSlow12 = 1.0f - fSlow11;
		float fSlow13 = float(fHslider2);
		float fSlow14 = 1.0f / (fSlow1 * fSlow6);
		float fSlow15 = 0.001f * float(fHslider3);
		int iSlow16 = std::fabs(fSlow15) < 1.1920929e-07f;
		float fSlow17 = ((iSlow16) ? 0.0f : std::exp(-(fConst2 / ((iSlow16) ? 1.0f : fSlow15))));
		float fSlow18 = 0.001f * fSlow8;
		int iSlow19 = std::fabs(fSlow18) < 1.1920929e-07f;
		float fSlow20 = ((iSlow19) ? 0.0f : std::exp(-(fConst2 / ((iSlow19) ? 1.0f : fSlow18))));
		float fSlow21 = 1.0f / std::max<float>(1.1920929e-07f, float(fHslider4)) + -1.0f;
		float fSlow22 = float(fHslider5);
		float fSlow23 = std::tan(fConst1 * float(fHslider6));
		float fSlow24 = FxMultiband_faustpower2_f(fSlow23);
		float fSlow25 = 1.0f / fSlow24;
		float fSlow26 = 2.0f * (1.0f - fSlow25);
		float fSlow27 = 1.0f / fSlow23;
		float fSlow28 = (fSlow27 + -1.4142135f) / fSlow23 + 1.0f;
		float fSlow29 = (fSlow27 + 1.4142135f) / fSlow23 + 1.0f;
		float fSlow30 = 1.0f / fSlow29;
		float fSlow31 = 1.0f / (fSlow24 * fSlow29);
		float fSlow32 = 1.0f / std::max<float>(1.1920929e-07f, float(fHslider7)) + -1.0f;
		float fSlow33 = float(fHslider8);
		float fSlow34 = 1.0f / std::max<float>(1.1920929e-07f, float(fHslider9)) + -1.0f;
		float fSlow35 = fConst3 * std::pow(1e+01f, 0.05f * float(fHslider10));
		for (int i0 = 0; i0 < count; i0 = i0 + 1) {
			float fTemp0 = float(input0[i0]);
			fRec1[0] = fTemp0 - fSlow7 * (fSlow5 * fRec1[2] + fSlow3 * fRec1[1]);
			fRec0[0] = fSlow7 * (fSlow2 * (fRec1[2] + (fRec1[0] - 2.0f * fRec1[1])) - (fSlow5 * fRec0[2] + fSlow3 * fRec0[1]));
			float fTemp1 = 2.0f * fRec0[1];
			float fTemp2 = float(input1[i0]);
			fRec5[0] = fTemp2 - fSlow7 * (fSlow5 * fRec5[2] + fSlow3 * fRec5[1]);
			fRec4[0] = fSlow7 * (fSlow2 * (fRec5[2] + (fRec5[0] - 2.0f * fRec5[1])) - (fSlow5 * fRec4[2] + fSlow3 * fRec4[1]));
			float fTemp3 = 2.0f * fRec4[1];
			float fTemp4 = std::fabs(std::fabs(fSlow14 * (fRec0[2] + (fRec0[0] - fTemp1))) + std::fabs(fSlow14 * (fRec4[2] + (fRec4[0] - fTemp3))));
			float fTemp5 = ((fTemp4 > fRec3[1]) ? fSlow20 : fSlow17);
			fRec3[0] = fTemp4 * (1.0f - fTemp5) + fRec3[1] * fTemp5;
			fRec2[0] = fSlow21 * std::max<float>(2e+01f * std::log10(std::max<float>(1.1754944e-38f, fRec3[0])) - fSlow13, 0.0f) * fSlow12 + fSlow11 * fRec2[1];
			float fTemp6 = std::pow(1e+01f, 0.05f * fRec2[0]);
			fRec11[0] = fTemp2 - fSlow30 * (fSlow28 * fRec11[2] + fSlow26 * fRec11[1]);
			float fTemp7 = 2.0f * fRec11[1];
			fRec10[0] = fSlow30 * (fSlow25 * (fRec11[2] + (fRec11[0] - fTemp7)) - (fSlow28 * fRec10[2] + fSlow26 * fRec10[1]));
			fRec9[0] = fSlow31 * (fRec10[2] + (fRec10[0] - 2.0f * fRec10[1])) - fSlow7 * (fSlow5 * fRec9[2] + fSlow3 * fRec9[1]);
			fRec8[0] = fSlow7 * (fRec9[2] + fRec9[0] + 2.0f * fRec9[1] - (fSlow5 * fRec8[2] + fSlow3 * fRec8[1]));
			float fTemp8 = fRec8[2] + fRec8[0] + 2.0f * fRec8[1];
			fRec15[0] = fTemp0 - fSlow30 * (fSlow28 * fRec15[2] + fSlow26 * fRec15[1]);
			float fTemp9 = 2.0f * fRec15[1];
			fRec14[0] = fSlow30 * (fSlow25 * (fRec15[2] + (fRec15[0] - fTemp9)) - (fSlow28 * fRec14[2] + fSlow26 * fRec14[1]));
			fRec13[0] = fSlow31 * (fRec14[2] + (fRec14[0] - 2.0f * fRec14[1])) - fSlow7 * (fSlow5 * fRec13[2] + fSlow3 * fRec13[1]);
			fRec12[0] = fSlow7 * (fRec13[2] + fRec13[0] + 2.0f * fRec13[1] - (fSlow5 * fRec12[2] + fSlow3 * fRec12[1]));
			float fTemp10 = fRec12[2] + fRec12[0] + 2.0f * fRec12[1];
			float fTemp11 = std::fabs(std::fabs(fSlow7 * fTemp10) + std::fabs(fSlow7 * fTemp8));
			float fTemp12 = ((fTemp11 > fRec7[1]) ? fSlow20 : fSlow17);
			fRec7[0] = fTemp11 * (1.0f - fTemp12) + fRec7[1] * fTemp12;
			fRec6[0] = fSlow32 * std::max<float>(2e+01f * std::log10(std::max<float>(1.1754944e-38f, fRec7[0])) - fSlow22, 0.0f) * fSlow12 + fSlow11 * fRec6[1];
			float fTemp13 = std::pow(1e+01f, 0.05f * fRec6[0]);
			fRec18[0] = fSlow30 * (fRec11[2] + fRec11[0] + fTemp7 - (fSlow28 * fRec18[2] + fSlow26 * fRec18[1]));
			float fTemp14 = fRec18[2] + fRec18[0] + 2.0f * fRec18[1];
			fRec19[0] = fSlow30 * (fRec15[2] + fRec15[0] + fTemp9 - (fSlow28 * fRec19[2] + fSlow26 * fRec19[1]));
			float fTemp15 = fRec19[2] + fRec19[0] + 2.0f * fRec19[1];
			float fTemp16 = std::fabs(std::fabs(fSlow30 * fTemp15) + std::fabs(fSlow30 * fTemp14));
			float fTemp17 = ((fTemp16 > fRec17[1]) ? fSlow20 : fSlow17);
			fRec17[0] = fTemp16 * (1.0f - fTemp17) + fRec17[1] * fTemp17;
			fRec16[0] = fSlow34 * std::max<float>(2e+01f * std::log10(std::max<float>(1.1754944e-38f, fRec17[0])) - fSlow33, 0.0f) * fSlow12 + fSlow11 * fRec16[1];
			float fTemp18 = std::pow(1e+01f, 0.05f * fRec16[0]);
			fRec20[0] = fSlow35 + fConst4 * fRec20[1];
			output0[i0] = FAUSTFLOAT(fRec20[0] * (fSlow30 * fTemp15 * fTemp18 + fSlow7 * (fTemp10 * fTemp13 + fSlow2 * fTemp6 * (fRec0[0] + fRec0[2] - fTemp1))));
			output1[i0] = FAUSTFLOAT(fRec20[0] * (fSlow30 * fTemp14 * fTemp18 + fSlow7 * (fTemp8 * fTemp13 + fSlow2 * fTemp6 * (fRec4[0] + fRec4[2] - fTemp3))));
			fRec1[2] = fRec1[1];
			fRec1[1] = fRec1[0];
			fRec0[2] = fRec0[1];
			fRec0[1] = fRec0[0];
			fRec5[2] = fRec5[1];
			fRec5[1] = fRec5[0];
			fRec4[2] = fRec4[1];
			fRec4[1] = fRec4[0];
			fRec3[1] = fRec3[0];
			fRec2[1] = fRec2[0];
			fRec11[2] = fRec11[1];
			fRec11[1] = fRec11[0];
			fRec10[2] = fRec10[1];
			fRec10[1] = fRec10[0];
			fRec9[2] = fRec9[1];
			fRec9[1] = fRec9[0];
			fRec8[2] = fRec8[1];
			fRec8[1] = fRec8[0];
			fRec15[2] = fRec15[1];
			fRec15[1] = fRec15[0];
			fRec14[2] = fRec14[1];
			fRec14[1] = fRec14[0];
			fRec13[2] = fRec13[1];
			fRec13[1] = fRec13[0];
			fRec12[2] = fRec12[1];
			fRec12[1] = fRec12[0];
			fRec7[1] = fRec7[0];
			fRec6[1] = fRec6[0];
			fRec18[2] = fRec18[1];
			fRec18[1] = fRec18[0];
			fRec19[2] = fRec19[1];
			fRec19[1] = fRec19[0];
			fRec17[1] = fRec17[0];
			fRec16[1] = fRec16[0];
			fRec20[1] = fRec20[0];
		}
	}

};

#endif
