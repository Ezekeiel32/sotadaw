/* ------------------------------------------------------------
name: "supersaw_fat"
Code generated with Faust 2.70.3 (https://faust.grame.fr)
Compilation options: -lang cpp -ct 1 -cn SupersawFat -es 1 -mcd 16 -mdd 1024 -mdy 33 -single -ftz 0
------------------------------------------------------------ */

#ifndef  __SupersawFat_H__
#define  __SupersawFat_H__

#ifndef FAUSTFLOAT
#define FAUSTFLOAT float
#endif 

/* link with : "" */
#include <algorithm>
#include <cmath>
#include <cstdint>
#include <math.h>

#ifndef FAUSTCLASS 
#define FAUSTCLASS SupersawFat
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

class SupersawFatSIG0 {
	
  private:
	
	int iVec2[2];
	int iRec4[2];
	
  public:
	
	int getNumInputsSupersawFatSIG0() {
		return 0;
	}
	int getNumOutputsSupersawFatSIG0() {
		return 1;
	}
	
	void instanceInitSupersawFatSIG0(int sample_rate) {
		for (int l5 = 0; l5 < 2; l5 = l5 + 1) {
			iVec2[l5] = 0;
		}
		for (int l6 = 0; l6 < 2; l6 = l6 + 1) {
			iRec4[l6] = 0;
		}
	}
	
	void fillSupersawFatSIG0(int count, float* table) {
		for (int i1 = 0; i1 < count; i1 = i1 + 1) {
			iVec2[0] = 1;
			iRec4[0] = (iVec2[1] + iRec4[1]) % 65536;
			table[i1] = std::sin(9.58738e-05f * float(iRec4[0]));
			iVec2[1] = iVec2[0];
			iRec4[1] = iRec4[0];
		}
	}

};

static SupersawFatSIG0* newSupersawFatSIG0() { return (SupersawFatSIG0*)new SupersawFatSIG0(); }
static void deleteSupersawFatSIG0(SupersawFatSIG0* dsp) { delete dsp; }

static float SupersawFat_faustpower2_f(float value) {
	return value * value;
}
static float ftbl0SupersawFatSIG0[65536];

class SupersawFat : public dsp {
	
 private:
	
	int iVec0[2];
	int fSampleRate;
	float fConst0;
	float fConst1;
	float fConst2;
	FAUSTFLOAT fHslider0;
	float fRec0[2];
	float fConst3;
	FAUSTFLOAT fButton0;
	float fVec1[2];
	int iRec1[2];
	float fConst4;
	float fRec2[2];
	float fConst5;
	float fConst6;
	float fConst7;
	FAUSTFLOAT fHslider1;
	float fConst8;
	float fRec5[2];
	FAUSTFLOAT fHslider2;
	FAUSTFLOAT fHslider3;
	float fConst9;
	float fRec6[2];
	float fRec8[2];
	float fRec10[2];
	float fRec12[2];
	float fRec14[2];
	float fRec16[2];
	float fRec18[2];
	float fRec3[3];
	FAUSTFLOAT fHslider4;
	float fRec20[3];
	
 public:
	SupersawFat() {}

	void metadata(Meta* m) { 
		m->declare("basics.lib/name", "Faust Basic Element Library");
		m->declare("basics.lib/tabulateNd", "Copyright (C) 2023 Bart Brouns <bart@magnetophon.nl>");
		m->declare("basics.lib/version", "1.12.0");
		m->declare("compile_options", "-lang cpp -ct 1 -cn SupersawFat -es 1 -mcd 16 -mdd 1024 -mdy 33 -single -ftz 0");
		m->declare("envelopes.lib/adsr:author", "Yann Orlarey and Andrey Bundin");
		m->declare("envelopes.lib/author", "GRAME");
		m->declare("envelopes.lib/copyright", "GRAME");
		m->declare("envelopes.lib/license", "LGPL with exception");
		m->declare("envelopes.lib/name", "Faust Envelope Library");
		m->declare("envelopes.lib/version", "1.3.0");
		m->declare("filename", "supersaw_fat.dsp");
		m->declare("filters.lib/fir:author", "Julius O. Smith III");
		m->declare("filters.lib/fir:copyright", "Copyright (C) 2003-2019 by Julius O. Smith III <jos@ccrma.stanford.edu>");
		m->declare("filters.lib/fir:license", "MIT-style STK-4.3 license");
		m->declare("filters.lib/iir:author", "Julius O. Smith III");
		m->declare("filters.lib/iir:copyright", "Copyright (C) 2003-2019 by Julius O. Smith III <jos@ccrma.stanford.edu>");
		m->declare("filters.lib/iir:license", "MIT-style STK-4.3 license");
		m->declare("filters.lib/lowpass0_highpass1", "MIT-style STK-4.3 license");
		m->declare("filters.lib/name", "Faust Filters Library");
		m->declare("filters.lib/resonlp:author", "Julius O. Smith III");
		m->declare("filters.lib/resonlp:copyright", "Copyright (C) 2003-2019 by Julius O. Smith III <jos@ccrma.stanford.edu>");
		m->declare("filters.lib/resonlp:license", "MIT-style STK-4.3 license");
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
		m->declare("name", "supersaw_fat");
		m->declare("oscillators.lib/name", "Faust Oscillator Library");
		m->declare("oscillators.lib/saw2ptr:author", "Julius O. Smith III");
		m->declare("oscillators.lib/saw2ptr:license", "STK-4.3");
		m->declare("oscillators.lib/version", "1.5.0");
		m->declare("platform.lib/name", "Generic Platform Library");
		m->declare("platform.lib/version", "1.3.0");
		m->declare("signals.lib/name", "Faust Signal Routing Library");
		m->declare("signals.lib/version", "1.5.0");
	}

	virtual int getNumInputs() {
		return 0;
	}
	virtual int getNumOutputs() {
		return 2;
	}
	
	static void classInit(int sample_rate) {
		SupersawFatSIG0* sig0 = newSupersawFatSIG0();
		sig0->instanceInitSupersawFatSIG0(sample_rate);
		sig0->fillSupersawFatSIG0(65536, ftbl0SupersawFatSIG0);
		deleteSupersawFatSIG0(sig0);
	}
	
	virtual void instanceConstants(int sample_rate) {
		fSampleRate = sample_rate;
		fConst0 = std::min<float>(1.92e+05f, std::max<float>(1.0f, float(fSampleRate)));
		fConst1 = 44.1f / fConst0;
		fConst2 = 1.0f - fConst1;
		fConst3 = 3.1415927f / fConst0;
		fConst4 = 1.0f / std::max<float>(1.0f, 0.22f * fConst0);
		fConst5 = std::max<float>(1.0f, 0.012f * fConst0);
		fConst6 = 1.0f / fConst5;
		fConst7 = 0.2f / std::max<float>(1.0f, 0.25f * fConst0);
		fConst8 = 0.5f / fConst0;
		fConst9 = 1.0f / fConst0;
	}
	
	virtual void instanceResetUserInterface() {
		fHslider0 = FAUSTFLOAT(9e+03f);
		fButton0 = FAUSTFLOAT(0.0f);
		fHslider1 = FAUSTFLOAT(2.2e+02f);
		fHslider2 = FAUSTFLOAT(0.35f);
		fHslider3 = FAUSTFLOAT(0.6f);
		fHslider4 = FAUSTFLOAT(0.7f);
	}
	
	virtual void instanceClear() {
		for (int l0 = 0; l0 < 2; l0 = l0 + 1) {
			iVec0[l0] = 0;
		}
		for (int l1 = 0; l1 < 2; l1 = l1 + 1) {
			fRec0[l1] = 0.0f;
		}
		for (int l2 = 0; l2 < 2; l2 = l2 + 1) {
			fVec1[l2] = 0.0f;
		}
		for (int l3 = 0; l3 < 2; l3 = l3 + 1) {
			iRec1[l3] = 0;
		}
		for (int l4 = 0; l4 < 2; l4 = l4 + 1) {
			fRec2[l4] = 0.0f;
		}
		for (int l7 = 0; l7 < 2; l7 = l7 + 1) {
			fRec5[l7] = 0.0f;
		}
		for (int l8 = 0; l8 < 2; l8 = l8 + 1) {
			fRec6[l8] = 0.0f;
		}
		for (int l9 = 0; l9 < 2; l9 = l9 + 1) {
			fRec8[l9] = 0.0f;
		}
		for (int l10 = 0; l10 < 2; l10 = l10 + 1) {
			fRec10[l10] = 0.0f;
		}
		for (int l11 = 0; l11 < 2; l11 = l11 + 1) {
			fRec12[l11] = 0.0f;
		}
		for (int l12 = 0; l12 < 2; l12 = l12 + 1) {
			fRec14[l12] = 0.0f;
		}
		for (int l13 = 0; l13 < 2; l13 = l13 + 1) {
			fRec16[l13] = 0.0f;
		}
		for (int l14 = 0; l14 < 2; l14 = l14 + 1) {
			fRec18[l14] = 0.0f;
		}
		for (int l15 = 0; l15 < 3; l15 = l15 + 1) {
			fRec3[l15] = 0.0f;
		}
		for (int l16 = 0; l16 < 3; l16 = l16 + 1) {
			fRec20[l16] = 0.0f;
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
	
	virtual SupersawFat* clone() {
		return new SupersawFat();
	}
	
	virtual int getSampleRate() {
		return fSampleRate;
	}
	
	virtual void buildUserInterface(UI* ui_interface) {
		ui_interface->openVerticalBox("supersaw_fat");
		ui_interface->addHorizontalSlider("cutoff", &fHslider0, FAUSTFLOAT(9e+03f), FAUSTFLOAT(2e+02f), FAUSTFLOAT(1.6e+04f), FAUSTFLOAT(1.0f));
		ui_interface->addHorizontalSlider("freq", &fHslider1, FAUSTFLOAT(2.2e+02f), FAUSTFLOAT(3e+01f), FAUSTFLOAT(2.5e+03f), FAUSTFLOAT(0.01f));
		ui_interface->addHorizontalSlider("gain", &fHslider4, FAUSTFLOAT(0.7f), FAUSTFLOAT(0.0f), FAUSTFLOAT(1.0f), FAUSTFLOAT(0.01f));
		ui_interface->addButton("gate", &fButton0);
		ui_interface->addHorizontalSlider("spread", &fHslider3, FAUSTFLOAT(0.6f), FAUSTFLOAT(0.0f), FAUSTFLOAT(1.0f), FAUSTFLOAT(0.01f));
		ui_interface->addHorizontalSlider("sub", &fHslider2, FAUSTFLOAT(0.35f), FAUSTFLOAT(0.0f), FAUSTFLOAT(1.0f), FAUSTFLOAT(0.01f));
		ui_interface->closeBox();
	}
	
	virtual void compute(int count, FAUSTFLOAT** RESTRICT inputs, FAUSTFLOAT** RESTRICT outputs) {
		FAUSTFLOAT* output0 = outputs[0];
		FAUSTFLOAT* output1 = outputs[1];
		float fSlow0 = fConst1 * float(fHslider0);
		float fSlow1 = float(fButton0);
		int iSlow2 = fSlow1 == 0.0f;
		float fSlow3 = float(fHslider1);
		float fSlow4 = fConst8 * fSlow3;
		float fSlow5 = float(fHslider2);
		float fSlow6 = float(fHslider3);
		float fSlow7 = 0.033f * fSlow6;
		float fSlow8 = std::max<float>(1.1920929e-07f, std::fabs(fSlow3 * (fSlow7 + 1.0f)));
		float fSlow9 = fConst9 * fSlow8;
		float fSlow10 = 1.0f - fConst0 / fSlow8;
		float fSlow11 = 0.022f * fSlow6;
		float fSlow12 = std::max<float>(1.1920929e-07f, std::fabs(fSlow3 * (fSlow11 + 1.0f)));
		float fSlow13 = fConst9 * fSlow12;
		float fSlow14 = 1.0f - fConst0 / fSlow12;
		float fSlow15 = 0.011f * fSlow6;
		float fSlow16 = std::max<float>(1.1920929e-07f, std::fabs(fSlow3 * (fSlow15 + 1.0f)));
		float fSlow17 = fConst9 * fSlow16;
		float fSlow18 = 1.0f - fConst0 / fSlow16;
		float fSlow19 = std::max<float>(1.1920929e-07f, std::fabs(fSlow3 * (1.0f - fSlow7)));
		float fSlow20 = fConst9 * fSlow19;
		float fSlow21 = 1.0f - fConst0 / fSlow19;
		float fSlow22 = std::max<float>(1.1920929e-07f, std::fabs(fSlow3));
		float fSlow23 = fConst9 * fSlow22;
		float fSlow24 = 1.0f - fConst0 / fSlow22;
		float fSlow25 = std::max<float>(1.1920929e-07f, std::fabs(fSlow3 * (1.0f - fSlow11)));
		float fSlow26 = fConst9 * fSlow25;
		float fSlow27 = 1.0f - fConst0 / fSlow25;
		float fSlow28 = std::max<float>(1.1920929e-07f, std::fabs(fSlow3 * (1.0f - fSlow15)));
		float fSlow29 = fConst9 * fSlow28;
		float fSlow30 = 1.0f - fConst0 / fSlow28;
		float fSlow31 = 0.16f * float(fHslider4);
		for (int i0 = 0; i0 < count; i0 = i0 + 1) {
			iVec0[0] = 1;
			fRec0[0] = fSlow0 + fConst2 * fRec0[1];
			float fTemp0 = std::tan(fConst3 * fRec0[0]);
			float fTemp1 = 1.0f / fTemp0;
			float fTemp2 = (fTemp1 + 0.90909094f) / fTemp0 + 1.0f;
			fVec1[0] = fSlow1;
			iRec1[0] = iSlow2 * (iRec1[1] + 1);
			fRec2[0] = fSlow1 + fRec2[1] * float(fVec1[1] >= fSlow1);
			float fTemp3 = std::max<float>(0.0f, std::min<float>(fConst6 * fRec2[0], std::max<float>(fConst7 * (fConst5 - fRec2[0]) + 1.0f, 0.8f)) * (1.0f - fConst4 * float(iRec1[0])));
			float fTemp4 = 1.0f - 1.0f / SupersawFat_faustpower2_f(fTemp0);
			float fTemp5 = (fTemp1 + -0.90909094f) / fTemp0 + 1.0f;
			float fTemp6 = ((1 - iVec0[1]) ? 0.0f : fSlow4 + fRec5[1]);
			fRec5[0] = fTemp6 - std::floor(fTemp6);
			float fTemp7 = fSlow5 * ftbl0SupersawFatSIG0[std::max<int>(0, std::min<int>(int(65536.0f * fRec5[0]), 65535))];
			float fTemp8 = fSlow9 + fRec6[1] + -1.0f;
			int iTemp9 = fTemp8 < 0.0f;
			float fTemp10 = fSlow9 + fRec6[1];
			fRec6[0] = ((iTemp9) ? fTemp10 : fTemp8);
			float fRec7 = ((iTemp9) ? fTemp10 : fSlow9 + fRec6[1] + fSlow10 * fTemp8);
			float fTemp11 = 2.0f * fRec7 + -1.0f;
			float fTemp12 = fSlow13 + fRec8[1] + -1.0f;
			int iTemp13 = fTemp12 < 0.0f;
			float fTemp14 = fSlow13 + fRec8[1];
			fRec8[0] = ((iTemp13) ? fTemp14 : fTemp12);
			float fRec9 = ((iTemp13) ? fTemp14 : fSlow13 + fRec8[1] + fSlow14 * fTemp12);
			float fTemp15 = 2.0f * fRec9 + -1.0f;
			float fTemp16 = fSlow17 + fRec10[1] + -1.0f;
			int iTemp17 = fTemp16 < 0.0f;
			float fTemp18 = fSlow17 + fRec10[1];
			fRec10[0] = ((iTemp17) ? fTemp18 : fTemp16);
			float fRec11 = ((iTemp17) ? fTemp18 : fSlow17 + fRec10[1] + fSlow18 * fTemp16);
			float fTemp19 = 2.0f * fRec11 + -1.0f;
			float fTemp20 = fSlow20 + fRec12[1] + -1.0f;
			int iTemp21 = fTemp20 < 0.0f;
			float fTemp22 = fSlow20 + fRec12[1];
			fRec12[0] = ((iTemp21) ? fTemp22 : fTemp20);
			float fRec13 = ((iTemp21) ? fTemp22 : fSlow20 + fRec12[1] + fSlow21 * fTemp20);
			float fTemp23 = 2.0f * fRec13 + -1.0f;
			float fTemp24 = fSlow23 + fRec14[1] + -1.0f;
			int iTemp25 = fTemp24 < 0.0f;
			float fTemp26 = fSlow23 + fRec14[1];
			fRec14[0] = ((iTemp25) ? fTemp26 : fTemp24);
			float fRec15 = ((iTemp25) ? fTemp26 : fSlow23 + fRec14[1] + fSlow24 * fTemp24);
			float fTemp27 = 2.0f * fRec15;
			float fTemp28 = fSlow26 + fRec16[1] + -1.0f;
			int iTemp29 = fTemp28 < 0.0f;
			float fTemp30 = fSlow26 + fRec16[1];
			fRec16[0] = ((iTemp29) ? fTemp30 : fTemp28);
			float fRec17 = ((iTemp29) ? fTemp30 : fSlow26 + fRec16[1] + fSlow27 * fTemp28);
			float fTemp31 = 2.0f * fRec17 + -1.0f;
			float fTemp32 = fSlow29 + fRec18[1] + -1.0f;
			int iTemp33 = fTemp32 < 0.0f;
			float fTemp34 = fSlow29 + fRec18[1];
			fRec18[0] = ((iTemp33) ? fTemp34 : fTemp32);
			float fRec19 = ((iTemp33) ? fTemp34 : fSlow29 + fRec18[1] + fSlow30 * fTemp32);
			float fTemp35 = 2.0f * fRec19 + -1.0f;
			fRec3[0] = 0.5f * fTemp35 + 0.7f * fTemp31 + fTemp27 + 0.9f * fTemp23 + 0.3f * fTemp19 + 0.2f * fTemp15 + 0.15f * fTemp11 + fTemp7 + (-1.0f - (fRec3[2] * fTemp5 + 2.0f * fRec3[1] * fTemp4) / fTemp2);
			output0[i0] = FAUSTFLOAT(tanhf(fSlow31 * ((fRec3[2] + fRec3[0] + 2.0f * fRec3[1]) * fTemp3 / fTemp2)));
			fRec20[0] = fTemp7 + 0.3f * fTemp35 + 0.2f * fTemp31 + fTemp27 + 0.15f * fTemp23 + 0.5f * fTemp19 + 0.7f * fTemp15 + 0.9f * fTemp11 + (-1.0f - (fTemp5 * fRec20[2] + 2.0f * fTemp4 * fRec20[1]) / fTemp2);
			output1[i0] = FAUSTFLOAT(tanhf(fSlow31 * (fTemp3 * (fRec20[2] + fRec20[0] + 2.0f * fRec20[1]) / fTemp2)));
			iVec0[1] = iVec0[0];
			fRec0[1] = fRec0[0];
			fVec1[1] = fVec1[0];
			iRec1[1] = iRec1[0];
			fRec2[1] = fRec2[0];
			fRec5[1] = fRec5[0];
			fRec6[1] = fRec6[0];
			fRec8[1] = fRec8[0];
			fRec10[1] = fRec10[0];
			fRec12[1] = fRec12[0];
			fRec14[1] = fRec14[0];
			fRec16[1] = fRec16[0];
			fRec18[1] = fRec18[0];
			fRec3[2] = fRec3[1];
			fRec3[1] = fRec3[0];
			fRec20[2] = fRec20[1];
			fRec20[1] = fRec20[0];
		}
	}

};

#endif
