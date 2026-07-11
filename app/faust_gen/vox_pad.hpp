/* ------------------------------------------------------------
name: "vox_pad"
Code generated with Faust 2.70.3 (https://faust.grame.fr)
Compilation options: -lang cpp -ct 1 -cn VoxPad -es 1 -mcd 16 -mdd 1024 -mdy 33 -single -ftz 0
------------------------------------------------------------ */

#ifndef  __VoxPad_H__
#define  __VoxPad_H__

#ifndef FAUSTFLOAT
#define FAUSTFLOAT float
#endif 

#include <algorithm>
#include <cmath>
#include <cstdint>
#include <math.h>

#ifndef FAUSTCLASS 
#define FAUSTCLASS VoxPad
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

class VoxPadSIG0 {
	
  private:
	
	int iVec1[2];
	int iRec1[2];
	
  public:
	
	int getNumInputsVoxPadSIG0() {
		return 0;
	}
	int getNumOutputsVoxPadSIG0() {
		return 1;
	}
	
	void instanceInitVoxPadSIG0(int sample_rate) {
		for (int l1 = 0; l1 < 2; l1 = l1 + 1) {
			iVec1[l1] = 0;
		}
		for (int l2 = 0; l2 < 2; l2 = l2 + 1) {
			iRec1[l2] = 0;
		}
	}
	
	void fillVoxPadSIG0(int count, float* table) {
		for (int i1 = 0; i1 < count; i1 = i1 + 1) {
			iVec1[0] = 1;
			iRec1[0] = (iVec1[1] + iRec1[1]) % 65536;
			table[i1] = std::sin(9.58738e-05f * float(iRec1[0]));
			iVec1[1] = iVec1[0];
			iRec1[1] = iRec1[0];
		}
	}

};

static VoxPadSIG0* newVoxPadSIG0() { return (VoxPadSIG0*)new VoxPadSIG0(); }
static void deleteVoxPadSIG0(VoxPadSIG0* dsp) { delete dsp; }

static float VoxPad_faustpower2_f(float value) {
	return value * value;
}
static float ftbl0VoxPadSIG0[65536];

class VoxPad : public dsp {
	
 private:
	
	int iVec0[2];
	FAUSTFLOAT fHslider0;
	int fSampleRate;
	float fConst0;
	float fConst1;
	float fConst2;
	float fRec2[2];
	FAUSTFLOAT fHslider1;
	FAUSTFLOAT fButton0;
	float fVec2[2];
	int iRec3[2];
	FAUSTFLOAT fHslider2;
	float fRec4[2];
	FAUSTFLOAT fHslider3;
	float fConst3;
	float fConst5;
	float fConst7;
	float fConst9;
	FAUSTFLOAT fHslider4;
	float fConst10;
	float fRec6[2];
	float fRec8[2];
	float fRec10[2];
	float fRec5[3];
	float fConst11;
	float fConst13;
	float fConst15;
	float fConst17;
	float fRec12[3];
	float fConst18;
	float fConst20;
	float fConst22;
	float fConst24;
	float fRec13[3];
	float fConst25;
	FAUSTFLOAT fHslider5;
	float fRec0[3];
	
 public:
	VoxPad() {}

	void metadata(Meta* m) { 
		m->declare("basics.lib/name", "Faust Basic Element Library");
		m->declare("basics.lib/tabulateNd", "Copyright (C) 2023 Bart Brouns <bart@magnetophon.nl>");
		m->declare("basics.lib/version", "1.12.0");
		m->declare("compile_options", "-lang cpp -ct 1 -cn VoxPad -es 1 -mcd 16 -mdd 1024 -mdy 33 -single -ftz 0");
		m->declare("envelopes.lib/adsr:author", "Yann Orlarey and Andrey Bundin");
		m->declare("envelopes.lib/author", "GRAME");
		m->declare("envelopes.lib/copyright", "GRAME");
		m->declare("envelopes.lib/license", "LGPL with exception");
		m->declare("envelopes.lib/name", "Faust Envelope Library");
		m->declare("envelopes.lib/version", "1.3.0");
		m->declare("filename", "vox_pad.dsp");
		m->declare("filters.lib/fir:author", "Julius O. Smith III");
		m->declare("filters.lib/fir:copyright", "Copyright (C) 2003-2019 by Julius O. Smith III <jos@ccrma.stanford.edu>");
		m->declare("filters.lib/fir:license", "MIT-style STK-4.3 license");
		m->declare("filters.lib/iir:author", "Julius O. Smith III");
		m->declare("filters.lib/iir:copyright", "Copyright (C) 2003-2019 by Julius O. Smith III <jos@ccrma.stanford.edu>");
		m->declare("filters.lib/iir:license", "MIT-style STK-4.3 license");
		m->declare("filters.lib/lowpass0_highpass1", "MIT-style STK-4.3 license");
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
		m->declare("name", "vox_pad");
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
		VoxPadSIG0* sig0 = newVoxPadSIG0();
		sig0->instanceInitVoxPadSIG0(sample_rate);
		sig0->fillVoxPadSIG0(65536, ftbl0VoxPadSIG0);
		deleteVoxPadSIG0(sig0);
	}
	
	virtual void instanceConstants(int sample_rate) {
		fSampleRate = sample_rate;
		fConst0 = std::min<float>(1.92e+05f, std::max<float>(1.0f, float(fSampleRate)));
		fConst1 = 3.1415927f / fConst0;
		fConst2 = 0.9f / fConst0;
		fConst3 = 0.15f / std::max<float>(1.0f, 0.4f * fConst0);
		float fConst4 = std::tan(2513.2742f / fConst0);
		fConst5 = 2.0f * (1.0f - 1.0f / VoxPad_faustpower2_f(fConst4));
		float fConst6 = 1.0f / fConst4;
		fConst7 = (fConst6 + -1.4142135f) / fConst4 + 1.0f;
		float fConst8 = (fConst6 + 1.4142135f) / fConst4 + 1.0f;
		fConst9 = 1.0f / fConst8;
		fConst10 = 1.0f / fConst0;
		fConst11 = 0.8f / fConst8;
		float fConst12 = std::tan(3298.6724f / fConst0);
		fConst13 = 2.0f * (1.0f - 1.0f / VoxPad_faustpower2_f(fConst12));
		float fConst14 = 1.0f / fConst12;
		fConst15 = (fConst14 + -0.18181819f) / fConst12 + 1.0f;
		float fConst16 = (fConst14 + 0.18181819f) / fConst12 + 1.0f;
		fConst17 = 1.0f / fConst16;
		fConst18 = 0.6f / (fConst12 * fConst16);
		float fConst19 = std::tan(2199.1147f / fConst0);
		fConst20 = 2.0f * (1.0f - 1.0f / VoxPad_faustpower2_f(fConst19));
		float fConst21 = 1.0f / fConst19;
		fConst22 = (fConst21 + -0.22222222f) / fConst19 + 1.0f;
		float fConst23 = (fConst21 + 0.22222222f) / fConst19 + 1.0f;
		fConst24 = 1.0f / fConst23;
		fConst25 = 1.3f / (fConst19 * fConst23);
	}
	
	virtual void instanceResetUserInterface() {
		fHslider0 = FAUSTFLOAT(3e+03f);
		fHslider1 = FAUSTFLOAT(0.04f);
		fButton0 = FAUSTFLOAT(0.0f);
		fHslider2 = FAUSTFLOAT(0.6f);
		fHslider3 = FAUSTFLOAT(0.25f);
		fHslider4 = FAUSTFLOAT(2.2e+02f);
		fHslider5 = FAUSTFLOAT(0.6f);
	}
	
	virtual void instanceClear() {
		for (int l0 = 0; l0 < 2; l0 = l0 + 1) {
			iVec0[l0] = 0;
		}
		for (int l3 = 0; l3 < 2; l3 = l3 + 1) {
			fRec2[l3] = 0.0f;
		}
		for (int l4 = 0; l4 < 2; l4 = l4 + 1) {
			fVec2[l4] = 0.0f;
		}
		for (int l5 = 0; l5 < 2; l5 = l5 + 1) {
			iRec3[l5] = 0;
		}
		for (int l6 = 0; l6 < 2; l6 = l6 + 1) {
			fRec4[l6] = 0.0f;
		}
		for (int l7 = 0; l7 < 2; l7 = l7 + 1) {
			fRec6[l7] = 0.0f;
		}
		for (int l8 = 0; l8 < 2; l8 = l8 + 1) {
			fRec8[l8] = 0.0f;
		}
		for (int l9 = 0; l9 < 2; l9 = l9 + 1) {
			fRec10[l9] = 0.0f;
		}
		for (int l10 = 0; l10 < 3; l10 = l10 + 1) {
			fRec5[l10] = 0.0f;
		}
		for (int l11 = 0; l11 < 3; l11 = l11 + 1) {
			fRec12[l11] = 0.0f;
		}
		for (int l12 = 0; l12 < 3; l12 = l12 + 1) {
			fRec13[l12] = 0.0f;
		}
		for (int l13 = 0; l13 < 3; l13 = l13 + 1) {
			fRec0[l13] = 0.0f;
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
	
	virtual VoxPad* clone() {
		return new VoxPad();
	}
	
	virtual int getSampleRate() {
		return fSampleRate;
	}
	
	virtual void buildUserInterface(UI* ui_interface) {
		ui_interface->openVerticalBox("vox_pad");
		ui_interface->addHorizontalSlider("attack", &fHslider3, FAUSTFLOAT(0.25f), FAUSTFLOAT(0.02f), FAUSTFLOAT(2.0f), FAUSTFLOAT(0.001f));
		ui_interface->addHorizontalSlider("freq", &fHslider4, FAUSTFLOAT(2.2e+02f), FAUSTFLOAT(2e+01f), FAUSTFLOAT(4e+03f), FAUSTFLOAT(0.001f));
		ui_interface->addHorizontalSlider("gain", &fHslider5, FAUSTFLOAT(0.6f), FAUSTFLOAT(0.0f), FAUSTFLOAT(1.0f), FAUSTFLOAT(0.01f));
		ui_interface->addButton("gate", &fButton0);
		ui_interface->addHorizontalSlider("release", &fHslider2, FAUSTFLOAT(0.6f), FAUSTFLOAT(0.05f), FAUSTFLOAT(3.0f), FAUSTFLOAT(0.001f));
		ui_interface->addHorizontalSlider("shimmer", &fHslider1, FAUSTFLOAT(0.04f), FAUSTFLOAT(0.0f), FAUSTFLOAT(0.15f), FAUSTFLOAT(0.001f));
		ui_interface->addHorizontalSlider("tone", &fHslider0, FAUSTFLOAT(3e+03f), FAUSTFLOAT(8e+02f), FAUSTFLOAT(8e+03f), FAUSTFLOAT(1.0f));
		ui_interface->closeBox();
	}
	
	virtual void compute(int count, FAUSTFLOAT** RESTRICT inputs, FAUSTFLOAT** RESTRICT outputs) {
		FAUSTFLOAT* output0 = outputs[0];
		FAUSTFLOAT* output1 = outputs[1];
		float fSlow0 = std::tan(fConst1 * float(fHslider0));
		float fSlow1 = 2.0f * (1.0f - 1.0f / VoxPad_faustpower2_f(fSlow0));
		float fSlow2 = 1.0f / fSlow0;
		float fSlow3 = (fSlow2 + -1.4142135f) / fSlow0 + 1.0f;
		float fSlow4 = (fSlow2 + 1.4142135f) / fSlow0 + 1.0f;
		float fSlow5 = 1.0f / fSlow4;
		float fSlow6 = float(fHslider1);
		float fSlow7 = float(fButton0);
		int iSlow8 = fSlow7 == 0.0f;
		float fSlow9 = 1.0f / std::max<float>(1.0f, fConst0 * float(fHslider2));
		float fSlow10 = std::max<float>(1.0f, fConst0 * float(fHslider3));
		float fSlow11 = 1.0f / fSlow10;
		float fSlow12 = float(fHslider4);
		float fSlow13 = std::max<float>(1.1920929e-07f, std::fabs(fSlow12));
		float fSlow14 = fConst10 * fSlow13;
		float fSlow15 = 1.0f - fConst0 / fSlow13;
		float fSlow16 = std::max<float>(1.1920929e-07f, std::fabs(0.996f * fSlow12));
		float fSlow17 = fConst10 * fSlow16;
		float fSlow18 = 1.0f - fConst0 / fSlow16;
		float fSlow19 = std::max<float>(1.1920929e-07f, std::fabs(1.004f * fSlow12));
		float fSlow20 = fConst10 * fSlow19;
		float fSlow21 = 1.0f - fConst0 / fSlow19;
		float fSlow22 = float(fHslider5);
		float fSlow23 = 0.393f / fSlow4;
		for (int i0 = 0; i0 < count; i0 = i0 + 1) {
			iVec0[0] = 1;
			float fTemp0 = ((1 - iVec0[1]) ? 0.0f : fConst2 + fRec2[1]);
			fRec2[0] = fTemp0 - std::floor(fTemp0);
			fVec2[0] = fSlow7;
			iRec3[0] = iSlow8 * (iRec3[1] + 1);
			fRec4[0] = fSlow7 + fRec4[1] * float(fVec2[1] >= fSlow7);
			float fTemp1 = fSlow14 + fRec6[1] + -1.0f;
			int iTemp2 = fTemp1 < 0.0f;
			float fTemp3 = fSlow14 + fRec6[1];
			fRec6[0] = ((iTemp2) ? fTemp3 : fTemp1);
			float fRec7 = ((iTemp2) ? fTemp3 : fSlow14 + fRec6[1] + fSlow15 * fTemp1);
			float fTemp4 = fSlow17 + fRec8[1] + -1.0f;
			int iTemp5 = fTemp4 < 0.0f;
			float fTemp6 = fSlow17 + fRec8[1];
			fRec8[0] = ((iTemp5) ? fTemp6 : fTemp4);
			float fRec9 = ((iTemp5) ? fTemp6 : fSlow17 + fRec8[1] + fSlow18 * fTemp4);
			float fTemp7 = fSlow20 + fRec10[1] + -1.0f;
			int iTemp8 = fTemp7 < 0.0f;
			float fTemp9 = fSlow20 + fRec10[1];
			fRec10[0] = ((iTemp8) ? fTemp9 : fTemp7);
			float fRec11 = ((iTemp8) ? fTemp9 : fSlow20 + fRec10[1] + fSlow21 * fTemp7);
			float fTemp10 = 0.33333334f * (2.0f * (fRec11 - (1.0f - (fRec9 + fRec7))) + -1.0f);
			fRec5[0] = fTemp10 - fConst9 * (fConst7 * fRec5[2] + fConst5 * fRec5[1]);
			fRec12[0] = fTemp10 - fConst17 * (fConst15 * fRec12[2] + fConst13 * fRec12[1]);
			fRec13[0] = fTemp10 - fConst24 * (fConst22 * fRec13[2] + fConst20 * fRec13[1]);
			fRec0[0] = fSlow22 * (fConst25 * (fRec13[0] - fRec13[2]) + fConst18 * (fRec12[0] - fRec12[2]) + fConst11 * (fRec5[2] + fRec5[0] + 2.0f * fRec5[1])) * std::max<float>(0.0f, std::min<float>(fSlow11 * fRec4[0], std::max<float>(fConst3 * (fSlow10 - fRec4[0]) + 1.0f, 0.85f)) * (1.0f - fSlow9 * float(iRec3[0]))) * (fSlow6 * ftbl0VoxPadSIG0[std::max<int>(0, std::min<int>(int(65536.0f * fRec2[0]), 65535))] + 1.0f) - fSlow5 * (fSlow3 * fRec0[2] + fSlow1 * fRec0[1]);
			float fTemp11 = fSlow23 * (fRec0[2] + fRec0[0] + 2.0f * fRec0[1]);
			output0[i0] = FAUSTFLOAT(fTemp11);
			output1[i0] = FAUSTFLOAT(fTemp11);
			iVec0[1] = iVec0[0];
			fRec2[1] = fRec2[0];
			fVec2[1] = fVec2[0];
			iRec3[1] = iRec3[0];
			fRec4[1] = fRec4[0];
			fRec6[1] = fRec6[0];
			fRec8[1] = fRec8[0];
			fRec10[1] = fRec10[0];
			fRec5[2] = fRec5[1];
			fRec5[1] = fRec5[0];
			fRec12[2] = fRec12[1];
			fRec12[1] = fRec12[0];
			fRec13[2] = fRec13[1];
			fRec13[1] = fRec13[0];
			fRec0[2] = fRec0[1];
			fRec0[1] = fRec0[0];
		}
	}

};

#endif
