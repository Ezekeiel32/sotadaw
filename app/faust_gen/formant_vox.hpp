/* ------------------------------------------------------------
name: "formant_vox"
Code generated with Faust 2.70.3 (https://faust.grame.fr)
Compilation options: -lang cpp -ct 1 -cn FormantVox -es 1 -mcd 16 -mdd 1024 -mdy 33 -single -ftz 0
------------------------------------------------------------ */

#ifndef  __FormantVox_H__
#define  __FormantVox_H__

#ifndef FAUSTFLOAT
#define FAUSTFLOAT float
#endif 

/* link with : "" */
#include <algorithm>
#include <cmath>
#include <cstdint>
#include <math.h>

#ifndef FAUSTCLASS 
#define FAUSTCLASS FormantVox
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

class FormantVoxSIG0 {
	
  private:
	
	int iVec2[2];
	int iRec7[2];
	
  public:
	
	int getNumInputsFormantVoxSIG0() {
		return 0;
	}
	int getNumOutputsFormantVoxSIG0() {
		return 1;
	}
	
	void instanceInitFormantVoxSIG0(int sample_rate) {
		for (int l5 = 0; l5 < 2; l5 = l5 + 1) {
			iVec2[l5] = 0;
		}
		for (int l6 = 0; l6 < 2; l6 = l6 + 1) {
			iRec7[l6] = 0;
		}
	}
	
	void fillFormantVoxSIG0(int count, float* table) {
		for (int i1 = 0; i1 < count; i1 = i1 + 1) {
			iVec2[0] = 1;
			iRec7[0] = (iVec2[1] + iRec7[1]) % 65536;
			table[i1] = std::sin(9.58738e-05f * float(iRec7[0]));
			iVec2[1] = iVec2[0];
			iRec7[1] = iRec7[0];
		}
	}

};

static FormantVoxSIG0* newFormantVoxSIG0() { return (FormantVoxSIG0*)new FormantVoxSIG0(); }
static void deleteFormantVoxSIG0(FormantVoxSIG0* dsp) { delete dsp; }

static float FormantVox_faustpower2_f(float value) {
	return value * value;
}
static float ftbl0FormantVoxSIG0[65536];

class FormantVox : public dsp {
	
 private:
	
	int iVec0[2];
	int fSampleRate;
	float fConst0;
	float fConst2;
	float fConst4;
	float fConst5;
	FAUSTFLOAT fHslider0;
	float fConst6;
	FAUSTFLOAT fButton0;
	float fVec1[2];
	int iRec2[2];
	FAUSTFLOAT fHslider1;
	float fRec3[2];
	FAUSTFLOAT fHslider2;
	float fConst7;
	int iRec4[2];
	FAUSTFLOAT fHslider3;
	FAUSTFLOAT fHslider4;
	float fConst8;
	float fRec8[2];
	FAUSTFLOAT fHslider5;
	FAUSTFLOAT fHslider6;
	float fRec5[2];
	float fRec1[3];
	float fRec9[3];
	float fRec10[3];
	FAUSTFLOAT fHslider7;
	float fRec0[3];
	
 public:
	FormantVox() {}

	void metadata(Meta* m) { 
		m->declare("basics.lib/name", "Faust Basic Element Library");
		m->declare("basics.lib/tabulateNd", "Copyright (C) 2023 Bart Brouns <bart@magnetophon.nl>");
		m->declare("basics.lib/version", "1.12.0");
		m->declare("compile_options", "-lang cpp -ct 1 -cn FormantVox -es 1 -mcd 16 -mdd 1024 -mdy 33 -single -ftz 0");
		m->declare("envelopes.lib/adsr:author", "Yann Orlarey and Andrey Bundin");
		m->declare("envelopes.lib/author", "GRAME");
		m->declare("envelopes.lib/copyright", "GRAME");
		m->declare("envelopes.lib/license", "LGPL with exception");
		m->declare("envelopes.lib/name", "Faust Envelope Library");
		m->declare("envelopes.lib/version", "1.3.0");
		m->declare("filename", "formant_vox.dsp");
		m->declare("filters.lib/fir:author", "Julius O. Smith III");
		m->declare("filters.lib/fir:copyright", "Copyright (C) 2003-2019 by Julius O. Smith III <jos@ccrma.stanford.edu>");
		m->declare("filters.lib/fir:license", "MIT-style STK-4.3 license");
		m->declare("filters.lib/iir:author", "Julius O. Smith III");
		m->declare("filters.lib/iir:copyright", "Copyright (C) 2003-2019 by Julius O. Smith III <jos@ccrma.stanford.edu>");
		m->declare("filters.lib/iir:license", "MIT-style STK-4.3 license");
		m->declare("filters.lib/lowpass0_highpass1", "Copyright (C) 2003-2019 by Julius O. Smith III <jos@ccrma.stanford.edu>");
		m->declare("filters.lib/lowpass0_highpass1:author", "Julius O. Smith III");
		m->declare("filters.lib/lowpass:author", "Julius O. Smith III");
		m->declare("filters.lib/lowpass:copyright", "Copyright (C) 2003-2019 by Julius O. Smith III <jos@ccrma.stanford.edu>");
		m->declare("filters.lib/lowpass:license", "MIT-style STK-4.3 license");
		m->declare("filters.lib/name", "Faust Filters Library");
		m->declare("filters.lib/resonbp:author", "Julius O. Smith III");
		m->declare("filters.lib/resonbp:copyright", "Copyright (C) 2003-2019 by Julius O. Smith III <jos@ccrma.stanford.edu>");
		m->declare("filters.lib/resonbp:license", "MIT-style STK-4.3 license");
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
		m->declare("name", "formant_vox");
		m->declare("noises.lib/name", "Faust Noise Generator Library");
		m->declare("noises.lib/version", "1.4.0");
		m->declare("oscillators.lib/name", "Faust Oscillator Library");
		m->declare("oscillators.lib/saw2ptr:author", "Julius O. Smith III");
		m->declare("oscillators.lib/saw2ptr:license", "STK-4.3");
		m->declare("oscillators.lib/version", "1.5.0");
		m->declare("platform.lib/name", "Generic Platform Library");
		m->declare("platform.lib/version", "1.3.0");
	}

	virtual int getNumInputs() {
		return 0;
	}
	virtual int getNumOutputs() {
		return 2;
	}
	
	static void classInit(int sample_rate) {
		FormantVoxSIG0* sig0 = newFormantVoxSIG0();
		sig0->instanceInitFormantVoxSIG0(sample_rate);
		sig0->fillFormantVoxSIG0(65536, ftbl0FormantVoxSIG0);
		deleteFormantVoxSIG0(sig0);
	}
	
	virtual void instanceConstants(int sample_rate) {
		fSampleRate = sample_rate;
		fConst0 = std::min<float>(1.92e+05f, std::max<float>(1.0f, float(fSampleRate)));
		float fConst1 = std::tan(28274.334f / fConst0);
		fConst2 = 2.0f * (1.0f - 1.0f / FormantVox_faustpower2_f(fConst1));
		float fConst3 = 1.0f / fConst1;
		fConst4 = (fConst3 + -1.4142135f) / fConst1 + 1.0f;
		fConst5 = 1.0f / ((fConst3 + 1.4142135f) / fConst1 + 1.0f);
		fConst6 = 3.1415927f / fConst0;
		fConst7 = 0.15f / std::max<float>(1.0f, 0.2f * fConst0);
		fConst8 = 1.0f / fConst0;
	}
	
	virtual void instanceResetUserInterface() {
		fHslider0 = FAUSTFLOAT(0.0f);
		fButton0 = FAUSTFLOAT(0.0f);
		fHslider1 = FAUSTFLOAT(0.25f);
		fHslider2 = FAUSTFLOAT(0.03f);
		fHslider3 = FAUSTFLOAT(0.12f);
		fHslider4 = FAUSTFLOAT(5.2f);
		fHslider5 = FAUSTFLOAT(0.006f);
		fHslider6 = FAUSTFLOAT(1.8e+02f);
		fHslider7 = FAUSTFLOAT(0.8f);
	}
	
	virtual void instanceClear() {
		for (int l0 = 0; l0 < 2; l0 = l0 + 1) {
			iVec0[l0] = 0;
		}
		for (int l1 = 0; l1 < 2; l1 = l1 + 1) {
			fVec1[l1] = 0.0f;
		}
		for (int l2 = 0; l2 < 2; l2 = l2 + 1) {
			iRec2[l2] = 0;
		}
		for (int l3 = 0; l3 < 2; l3 = l3 + 1) {
			fRec3[l3] = 0.0f;
		}
		for (int l4 = 0; l4 < 2; l4 = l4 + 1) {
			iRec4[l4] = 0;
		}
		for (int l7 = 0; l7 < 2; l7 = l7 + 1) {
			fRec8[l7] = 0.0f;
		}
		for (int l8 = 0; l8 < 2; l8 = l8 + 1) {
			fRec5[l8] = 0.0f;
		}
		for (int l9 = 0; l9 < 3; l9 = l9 + 1) {
			fRec1[l9] = 0.0f;
		}
		for (int l10 = 0; l10 < 3; l10 = l10 + 1) {
			fRec9[l10] = 0.0f;
		}
		for (int l11 = 0; l11 < 3; l11 = l11 + 1) {
			fRec10[l11] = 0.0f;
		}
		for (int l12 = 0; l12 < 3; l12 = l12 + 1) {
			fRec0[l12] = 0.0f;
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
	
	virtual FormantVox* clone() {
		return new FormantVox();
	}
	
	virtual int getSampleRate() {
		return fSampleRate;
	}
	
	virtual void buildUserInterface(UI* ui_interface) {
		ui_interface->openVerticalBox("formant_vox");
		ui_interface->addHorizontalSlider("attack", &fHslider2, FAUSTFLOAT(0.03f), FAUSTFLOAT(0.001f), FAUSTFLOAT(1.0f), FAUSTFLOAT(0.001f));
		ui_interface->addHorizontalSlider("breath", &fHslider3, FAUSTFLOAT(0.12f), FAUSTFLOAT(0.0f), FAUSTFLOAT(1.0f), FAUSTFLOAT(0.01f));
		ui_interface->addHorizontalSlider("freq", &fHslider6, FAUSTFLOAT(1.8e+02f), FAUSTFLOAT(4e+01f), FAUSTFLOAT(1.5e+03f), FAUSTFLOAT(0.001f));
		ui_interface->addHorizontalSlider("gain", &fHslider7, FAUSTFLOAT(0.8f), FAUSTFLOAT(0.0f), FAUSTFLOAT(1.0f), FAUSTFLOAT(0.01f));
		ui_interface->addButton("gate", &fButton0);
		ui_interface->addHorizontalSlider("release", &fHslider1, FAUSTFLOAT(0.25f), FAUSTFLOAT(0.02f), FAUSTFLOAT(2.0f), FAUSTFLOAT(0.001f));
		ui_interface->addHorizontalSlider("vibrate", &fHslider4, FAUSTFLOAT(5.2f), FAUSTFLOAT(0.0f), FAUSTFLOAT(8.0f), FAUSTFLOAT(0.01f));
		ui_interface->addHorizontalSlider("vibrato", &fHslider5, FAUSTFLOAT(0.006f), FAUSTFLOAT(0.0f), FAUSTFLOAT(0.03f), FAUSTFLOAT(0.0001f));
		ui_interface->addHorizontalSlider("vowel", &fHslider0, FAUSTFLOAT(0.0f), FAUSTFLOAT(0.0f), FAUSTFLOAT(1.0f), FAUSTFLOAT(0.001f));
		ui_interface->closeBox();
	}
	
	virtual void compute(int count, FAUSTFLOAT** RESTRICT inputs, FAUSTFLOAT** RESTRICT outputs) {
		FAUSTFLOAT* output0 = outputs[0];
		FAUSTFLOAT* output1 = outputs[1];
		float fSlow0 = float(fHslider0);
		int iSlow1 = fSlow0 < 0.5f;
		float fSlow2 = 2.0f * (fSlow0 + -0.5f);
		float fSlow3 = 2.0f * fSlow0;
		float fSlow4 = std::tan(fConst6 * ((iSlow1) ? 2.44e+03f * std::pow(1.2336066f, fSlow3) : 3.01e+03f * std::pow(0.74418604f, fSlow2)));
		float fSlow5 = 1.0f / fSlow4;
		float fSlow6 = (fSlow5 + 0.05882353f) / fSlow4 + 1.0f;
		float fSlow7 = fSlow4 * fSlow6;
		float fSlow8 = 1.0f - 1.0f / FormantVox_faustpower2_f(fSlow4);
		float fSlow9 = (fSlow5 + -0.05882353f) / fSlow4 + 1.0f;
		float fSlow10 = float(fButton0);
		int iSlow11 = fSlow10 == 0.0f;
		float fSlow12 = 1.0f / std::max<float>(1.0f, fConst0 * float(fHslider1));
		float fSlow13 = std::max<float>(1.0f, fConst0 * float(fHslider2));
		float fSlow14 = 1.0f / fSlow13;
		float fSlow15 = 2.3283064e-10f * float(fHslider3);
		float fSlow16 = fConst8 * float(fHslider4);
		float fSlow17 = float(fHslider5);
		float fSlow18 = float(fHslider6);
		float fSlow19 = std::tan(fConst6 * ((iSlow1) ? 1.09e+03f * std::pow(2.1009173f, fSlow3) : 2.29e+03f * std::pow(0.37991267f, fSlow2)));
		float fSlow20 = 1.0f / fSlow19;
		float fSlow21 = (fSlow20 + 0.071428575f) / fSlow19 + 1.0f;
		float fSlow22 = fSlow19 * fSlow21;
		float fSlow23 = 1.0f - 1.0f / FormantVox_faustpower2_f(fSlow19);
		float fSlow24 = (fSlow20 + -0.071428575f) / fSlow19 + 1.0f;
		float fSlow25 = std::tan(fConst6 * ((iSlow1) ? 7.3e+02f * std::pow(0.369863f, fSlow3) : 2.7e+02f * std::pow(1.1111112f, fSlow2)));
		float fSlow26 = 1.0f / fSlow25;
		float fSlow27 = (fSlow26 + 0.09090909f) / fSlow25 + 1.0f;
		float fSlow28 = fSlow25 * fSlow27;
		float fSlow29 = 1.0f - 1.0f / FormantVox_faustpower2_f(fSlow25);
		float fSlow30 = (fSlow26 + -0.09090909f) / fSlow25 + 1.0f;
		float fSlow31 = 0.3f * float(fHslider7);
		for (int i0 = 0; i0 < count; i0 = i0 + 1) {
			iVec0[0] = 1;
			fVec1[0] = fSlow10;
			iRec2[0] = iSlow11 * (iRec2[1] + 1);
			fRec3[0] = fSlow10 + fRec3[1] * float(fVec1[1] >= fSlow10);
			iRec4[0] = 1103515245 * iRec4[1] + 12345;
			float fTemp0 = ((1 - iVec0[1]) ? 0.0f : fSlow16 + fRec8[1]);
			fRec8[0] = fTemp0 - std::floor(fTemp0);
			float fTemp1 = std::max<float>(1.1920929e-07f, std::fabs(fSlow18 * (fSlow17 * ftbl0FormantVoxSIG0[std::max<int>(0, std::min<int>(int(65536.0f * fRec8[0]), 65535))] + 1.0f)));
			float fTemp2 = fRec5[1] + fConst8 * fTemp1;
			float fTemp3 = fTemp2 + -1.0f;
			int iTemp4 = fTemp3 < 0.0f;
			fRec5[0] = ((iTemp4) ? fTemp2 : fTemp3);
			float fRec6 = ((iTemp4) ? fTemp2 : fTemp2 + fTemp3 * (1.0f - fConst0 / fTemp1));
			float fTemp5 = (2.0f * fRec6 + fSlow15 * float(iRec4[0]) + -1.0f) * std::max<float>(0.0f, std::min<float>(fSlow14 * fRec3[0], std::max<float>(fConst7 * (fSlow13 - fRec3[0]) + 1.0f, 0.85f)) * (1.0f - fSlow12 * float(iRec2[0])));
			fRec1[0] = fTemp5 - (fRec1[2] * fSlow9 + 2.0f * fRec1[1] * fSlow8) / fSlow6;
			fRec9[0] = fTemp5 - (fRec9[2] * fSlow24 + 2.0f * fRec9[1] * fSlow23) / fSlow21;
			fRec10[0] = fTemp5 - (fRec10[2] * fSlow30 + 2.0f * fRec10[1] * fSlow29) / fSlow27;
			fRec0[0] = tanhf(fSlow31 * ((fRec10[0] - fRec10[2]) / fSlow28 + 0.55f * ((fRec9[0] - fRec9[2]) / fSlow22) + 0.32f * ((fRec1[0] - fRec1[2]) / fSlow7))) - fConst5 * (fConst4 * fRec0[2] + fConst2 * fRec0[1]);
			float fTemp6 = fConst5 * (fRec0[2] + fRec0[0] + 2.0f * fRec0[1]);
			output0[i0] = FAUSTFLOAT(fTemp6);
			output1[i0] = FAUSTFLOAT(fTemp6);
			iVec0[1] = iVec0[0];
			fVec1[1] = fVec1[0];
			iRec2[1] = iRec2[0];
			fRec3[1] = fRec3[0];
			iRec4[1] = iRec4[0];
			fRec8[1] = fRec8[0];
			fRec5[1] = fRec5[0];
			fRec1[2] = fRec1[1];
			fRec1[1] = fRec1[0];
			fRec9[2] = fRec9[1];
			fRec9[1] = fRec9[0];
			fRec10[2] = fRec10[1];
			fRec10[1] = fRec10[0];
			fRec0[2] = fRec0[1];
			fRec0[1] = fRec0[0];
		}
	}

};

#endif
